import os
import folder_paths

import torchaudio
from torchaudio.models import hdemucs_high
import torch

from dataclasses import dataclass
from typing import Callable
from functools import partial

separation_model = "hdemucs_high_trained.pt"


@dataclass
class SourceSeparationBundle:
    _model_path: str
    _model_factory_func: Callable[[], torch.nn.Module]
    _sample_rate: int

    @property
    def sample_rate(self) -> int:
        return self._sample_rate

    def get_model(self) -> torch.nn.Module:
        model = self._model_factory_func()        
        separation_model_path = os.path.join(folder_paths.models_dir, self._model_path)
        state_dict = torch.load(separation_model_path)

        model.load_state_dict(state_dict)
        model.eval()
        return model


HDEMUCS_HIGH_MUSDB_PLUS = SourceSeparationBundle(
    _model_path="Separation/hdemucs_high_trained.pt",
    _model_factory_func=partial(hdemucs_high, sources=["drums", "bass", "other", "vocals"]),
    _sample_rate=44100,
)