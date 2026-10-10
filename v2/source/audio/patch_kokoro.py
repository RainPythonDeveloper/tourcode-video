"""Expose Kokoro's per-phoneme durations as a model output named "duration".

kokoro-onnx reads that output to report when every phoneme is spoken, which is
what syncs the on-screen words to the voice.
Usage: python patch_kokoro.py kokoro-v1.0.onnx kokoro-v1.0-timed.onnx
"""
import sys

import onnx
from onnx import TensorProto, helper

src, dst = sys.argv[1], sys.argv[2]
model = onnx.load(src)
graph = model.graph
clip = "/encoder/Clip_output_0"  # rounded, clipped durations from the duration predictor
graph.node.append(helper.make_node("Cast", [clip], ["duration"], to=TensorProto.INT64))
graph.output.append(helper.make_tensor_value_info("duration", TensorProto.INT64, ["phonemes"]))
onnx.save(model, dst)
print("wrote", dst)
