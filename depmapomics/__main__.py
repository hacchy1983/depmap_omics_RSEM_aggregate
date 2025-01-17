"""Implement CDS genomics pipeline command line utility."""
import fire
import os

os.environ["DEPMAP_ENV"] = "PROD"
from depmapomics import env_config
from depmapomics import dm_omics


class Command(object):
    """A command line to drive the omics pipeline modules."""

    def end_to_end(self):
        """End to end interface."""
        raise NotImplementedError

    def expression_postprocess(self):
        """Running gene expression post-processing."""
        raise NotImplementedError

    async def mutation_postprocess(self):
        print(os.environ["DEPMAP_ENV"])
        await dm_omics.mutationPostProcessing(
            wesrefworkspace=env_config.WESCNWORKSPACE,
            wgsrefworkspace=env_config.WGSWORKSPACE,
        )


def main():
    """Main function of command utility."""
    fire.Fire(Command)


if __name__ == "__main__":
    main()
