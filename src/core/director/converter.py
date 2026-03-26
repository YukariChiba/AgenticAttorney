import json
import logging
from pathlib import Path

from autogen_agentchat.messages import StructuredMessage, TextMessage
from autogen_core.models import ChatCompletionClient
from openai import LengthFinishReasonError

from src.agents.factory import AgentFactory
from src.constants import TAGS_JSON
from src.core.director.assets import AssetsManager
from src.core.director.prompts import PromptBuilder
from src.core.director.validate import FrameValidator
from src.prompts.engine import TemplateEngine
from src.types.config import AppConfig
from src.types.director.data import DirectorData
from src.types.director.frames import DirectorFrame, Frame, FrameList
from src.types.director.presets import Character
from src.types.logfile import LogEntry


class LogConverter:
    def __init__(
        self, assets_manager: AssetsManager, logs: list[LogEntry], config: AppConfig
    ):
        self.assets = assets_manager
        self.music = assets_manager.fetch_music()
        self.sounds = assets_manager.fetch_sounds()
        self.tags = json.load(open(TAGS_JSON, encoding="utf-8"))
        self.config = config
        self.validator = FrameValidator(assets_manager)
        self.prompt_builder = PromptBuilder(
            active_characters=self._extract_active_characters(logs),
            music=self.music,
            sounds=self.sounds,
            tags=self.tags,
        )

        # create agent
        template_engine: TemplateEngine = TemplateEngine(self.config)
        system_template = template_engine._load_raw_content("director/system")
        system_msg = self.prompt_builder.build_system_prompt(system_template)
        model_config = self.config.director.model.to_component_config()
        model_client = ChatCompletionClient.load_component(model_config)
        factory = AgentFactory(self.config, model_client, template_engine)
        self.agent = factory.create_objection_agent(system_msg)

    def _extract_active_characters(self, logs: list[LogEntry]) -> list[Character]:
        active_char_ids = set()
        active_characters = []
        for log_entry in logs:
            char_id = log_entry.objlol_id

            if char_id in active_char_ids:
                continue

            active_char_ids.add(char_id)
            char_info = self.assets.get_character_info(char_id)
            if char_info:
                active_characters.append(char_info)

        return active_characters

    async def _process_log_entry(
        self,
        log_entry: LogEntry,
        next_log_entry: LogEntry | None,
        previous_frames: list[Frame],
        frame_id: int,
    ) -> tuple[list[DirectorFrame], list[Frame]]:
        template_engine: TemplateEngine = TemplateEngine(self.config)
        user_template = template_engine._load_raw_content("director/user")
        user_msg = self.prompt_builder.build_user_prompt(
            user_template, log_entry, next_log_entry, previous_frames, self.assets
        )

        frame_list: FrameList | None = None
        max_retries = self.config.director.max_retries

        for retry_count in range(max_retries):
            validation_errors = []

            try:
                message = TextMessage(source="user", content=user_msg)
                response = await self.agent.run(
                    task=message, output_task_messages=False
                )

                frame_list = None
                for msg in response.messages:
                    if isinstance(msg, StructuredMessage):
                        if isinstance(msg.content, FrameList):
                            frame_list = msg.content
                            continue

            except LengthFinishReasonError as e:
                logging.warning(f"Token limit exceeded: {e}")
                validation_errors.append(
                    "Your previous output for this log is too long, please reduce it."
                )
                frame_list = FrameList([])

            except Exception as e:
                logging.error(f"Error processing log entry: {e}", exc_info=True)
                return [], []

            if frame_list is None:
                logging.warning("No valid frame list generated")
                return [], []

            for i, frame in enumerate(frame_list.root, start=1):
                error = self.validator.validate_frame(frame, i)
                if error:
                    validation_errors.append(error)

            if not validation_errors:
                break

            if retry_count < max_retries - 1:
                logging.warning(
                    f"Validation errors found (attempt {retry_count + 1}/{max_retries}): {validation_errors}"
                )
                errors_str = "\n".join(validation_errors)
                user_msg += f"The previous response had validation errors:\n{errors_str}\n\nPlease fix these errors and regenerate the entire response."
        else:
            logging.warning(
                f"Failed validation after {max_retries} attempts, using original fallback logic"
            )

        if frame_list is None:
            return [], []

        speaker_frames = []

        for frame in frame_list.root:
            char_data = self.assets.get_character_info(frame.character)
            if not char_data:
                continue

            bg_id = (
                self.assets.get_background_id(char_data.side)
                if char_data.side
                else None
            )

            director_frame = DirectorFrame.from_frame(frame, bg_id, frame_id)
            speaker_frames.append(director_frame)

            new_frame = Frame.model_validate(frame.model_dump())
            previous_frames.append(new_frame)

            frame_id += 1

        logging.info(f"Processed {len(speaker_frames)} frames")

        return speaker_frames, previous_frames

    async def process_sequence(self, logs: list[LogEntry]) -> list[DirectorFrame]:
        all_frames = []
        previous_frames = []
        frame_id = 1

        total_logs = len(logs)
        for i, log_entry in enumerate(logs, 1):
            logging.info(f"Processing log entry {i}/{total_logs}")

            next_log_entry = logs[i] if i < total_logs else None

            recent_frames = (
                previous_frames[-10:]
                if len(previous_frames) > 10
                else previous_frames[:]
            )

            speaker_frames, previous_frames = await self._process_log_entry(
                log_entry, next_log_entry, recent_frames, frame_id
            )

            all_frames.extend(speaker_frames)
            frame_id = len(all_frames) + 1

        return all_frames

    def load_log_file(self, filepath: str | Path) -> list[LogEntry]:
        with open(filepath, "r", encoding="utf-8") as f:
            logs_data = json.load(f)
        return [LogEntry.model_validate(log) for log in logs_data]

    def save_director_file(self, frames: list[DirectorFrame], output_path: str) -> None:
        frames_dict = [frame.to_dict() for frame in frames]

        director_data = DirectorData.from_frames(frames_dict)
        director_data.to_file(output_path)

        logging.info(f"Saved director file to {output_path}")
