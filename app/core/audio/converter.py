from pathlib import Path

import soundfile as sf


class AudioConverter:

    @staticmethod
    def wav_to_ogg(
        source: Path,
        destination: Path,
    ) -> Path:

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        data, samplerate = sf.read(str(source))

        try:
            sf.write(
                str(destination),
                data,
                samplerate,
                format="OGG",
                subtype="OPUS",
            )

        except Exception as ex:

            print(
                "Opus unavailable, falling back to Vorbis:",
                ex,
            )

            sf.write(
                str(destination),
                data,
                samplerate,
                format="OGG",
                subtype="VORBIS",
            )

        return destination