from deeprhythm import DeepRhythmPredictor

model = DeepRhythmPredictor()
tempo = model.predict("Music+Beatmaps/sink.mp3")
print(f"Predicted Tempo: {tempo} BPM")