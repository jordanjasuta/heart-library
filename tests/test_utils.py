# MIT License
#
# Copyright (C) The Adversarial Robustness Toolbox (HEART) Authors 2024
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging

from tests.utils import HEARTTestException
import pytest


logger = logging.getLogger(__name__)


def test_process_inputs_for_art(heart_warning):
    try:
        from heart_library.utils import process_inputs_for_art
        from datasets import load_dataset
        import numpy as np
        import torchvision
        import torch
        
        # define HF dataset and convert to art
        data = load_dataset("cifar10", split="test[0:10]")
        x, y, m = process_inputs_for_art(data)
        assert isinstance(x, np.ndarray)
        assert isinstance(y, np.ndarray)
        assert isinstance(m, list)
        
        # define torchvision dataset and convert to art
        data = torchvision.datasets.CIFAR10("../../data", train=False, download=True)
        data = torch.utils.data.Subset(data, list(range(10)))
        x, y, m = process_inputs_for_art(data)
        assert isinstance(x, np.ndarray)
        assert isinstance(y, np.ndarray)
        assert isinstance(m, list)
        
        # define HF dataset, select subset, convert to art
        data = load_dataset("cifar10", split="test[0:10]")
        data = torch.utils.data.Subset(data, list(range(10)))
        x, y, m = process_inputs_for_art(data)
        assert isinstance(x, np.ndarray)
        assert isinstance(y, np.ndarray)
        assert isinstance(m, list)
        
        # define dict of data and convert to art
        data = {"images": x, "labels": y, "metadata": m}
        x, y, m = process_inputs_for_art(data)
        assert isinstance(x, np.ndarray)
        assert isinstance(y, np.ndarray)
        assert isinstance(m, list)
        
        data = {"images": x, "labels": y}
        x, y, _ = process_inputs_for_art(data)
        assert isinstance(x, np.ndarray)
        assert isinstance(y, np.ndarray)
        
        data = {"images": x}
        x, _, _ = process_inputs_for_art(data)
        assert isinstance(x, np.ndarray)
        
        # define a tuple and convert to art
        data = (x, y, m)
        x, y, m = process_inputs_for_art(data)
        assert isinstance(x, np.ndarray)
        assert isinstance(y, np.ndarray)
        assert isinstance(m, list)
        
        targets = [{"boxes": np.array([0]), "scores": np.array([0]), "labels": np.array([0])}]
        data = (x, targets, m)
        x, y, m = process_inputs_for_art(data)
        assert isinstance(x, np.ndarray)
        assert isinstance(y, np.ndarray)
        assert isinstance(m, list)
        
        # tuple does not contain 3 items
        with pytest.raises(IndexError):
            data = (x, y)
            x, y, m = process_inputs_for_art(data)
        
        # define sequence and convert to art
        data = np.expand_dims(x, axis=0)
        x, y, m = process_inputs_for_art(data)
        assert isinstance(x, np.ndarray)
        assert isinstance(m, list)
        
        # define a tensor and convert to art
        data = torch.Tensor(x)
        x, y, m = process_inputs_for_art(data)
        assert isinstance(x, np.ndarray)
        
        # define an np.ndarray and convert to art
        x, y, m = process_inputs_for_art(x)
        assert isinstance(x, np.ndarray)
        
        # huggingface iterable dataset 
        from functools import partial
        from datasets import Dataset
        NUM_SAMPLES = 5
        data = load_dataset("cifar10", split="test", streaming=True)
        sample_data = data.take(NUM_SAMPLES)
        def gen_from_iterable_dataset(iterable_ds):
            yield from iterable_ds
        data = Dataset.from_generator(partial(gen_from_iterable_dataset, sample_data), features=sample_data.features)
        x, _, _ = process_inputs_for_art(sample_data)
        assert isinstance(x, np.ndarray)
        
        # targeted dataset
        from typing import Tuple, Dict, Any
        class TargetedImageDataset:
            def __init__(self, images):
                self.images = images
            def __len__(self)->int:
                return len(self.images)
            def __getitem__(self, ind: int) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
                image = self.images[ind]
                return image, 2, {}
        data = TargetedImageDataset(x)
        x, y, m = process_inputs_for_art(data)
        assert isinstance(x, np.ndarray)
        assert isinstance(y, np.ndarray)
        assert isinstance(m, list)

    except HEARTTestException as e:
        heart_warning(e)


def test_hf_dataset_to_maite(heart_warning):
    try:
        from heart_library.utils import hf_dataset_to_maite
        import maite.protocols.image_classification as ic
        from datasets import load_dataset
        
        # define HF dataset and convert to art
        data = load_dataset("cifar10", split="test[0:10]")
        maite_dataset = hf_dataset_to_maite(data)
        assert isinstance(maite_dataset, ic.Dataset)
        

    except HEARTTestException as e:
        heart_warning(e)


def test_subset_to_maite(heart_warning):
    try:
        
        import torchvision
        import torch
        import maite.protocols.image_classification as ic
        
        # define torchvision subset dataset and convert to art
        data = torchvision.datasets.CIFAR10("../data", train=False, download=True)
        maite_dataset = torch.utils.data.Subset(data, list(range(10)))
        assert isinstance(maite_dataset, ic.Dataset)
        

    except HEARTTestException as e:
        heart_warning(e)
        
        
def test_image_dataset(heart_warning):
    try:
        from heart_library.utils import ImageDataset
        import maite.protocols.image_classification as ic
        import numpy as np
        
        x = [np.array([0])]
        y = np.array([0])
        m = [{}]
        dataset = ImageDataset(x, y, m)
        assert isinstance(dataset, ic.Dataset)
        x1, y1, m1 = dataset[0]
        assert x1 == x[0]
        assert y1 == y[0]
        assert m1 == m[0]
        assert len(dataset) == 1

    except HEARTTestException as e:
        heart_warning(e)