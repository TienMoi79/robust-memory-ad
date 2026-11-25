"""Fill with Phuc's exact pipeline after the baseline handoff.

This is intentionally not a guessed implementation of the upstream model.
Run: python -m scripts.profile --config YOUR_CONFIG.json
     --adapter examples.adapter_template:create_adapter --output outputs/UNIQUE_ID
"""


class Adapter:
    def load(self, config, base):
        # Verify actual baseline git HEAD equals config['baseline_commit'] here.
        # Load model + bank once; set eval(); fix dtype/seed/query configuration.
        raise NotImplementedError('Waiting for Phuc: commit, load command, bank and preprocessing')

    def decode(self, spec, base):
        # Return an independent decoded image in host RAM; no preprocessing yet.
        # All file paths are relative to the config file directory (`base`).
        raise NotImplementedError('Use the exact decoder/channel order agreed with Phuc')

    def predict(self, image):
        # Preprocess from decoded RAM, batch 1, transfer, backbone, query, score/map.
        # Do not load bank, read files, cache predictions or lazily yield output here.
        # Ensure inference_mode/no_grad on CPU too. If needed return CPU output here.
        raise NotImplementedError('Wire the exact one-image inference function')

    def image_score(self, result):
        raise NotImplementedError('Extract the raw score matching predictions.csv')

    def synchronize(self):
        # Harness already syncs the selected PyTorch device on CUDA.
        # Add any external FAISS/custom CUDA stream synchronization required.
        pass


def create_adapter():
    return Adapter()
