import wave
import sys

import pyaudio


CHUNK = 1024*64
FRAME_SHIFT = 6000


def playWithShift(filePath: str):
    with wave.open(filePath, "rb") as wf:
        # Instantiate PyAudio and initialize PortAudio system resources (1)
        p = pyaudio.PyAudio()

        # Open stream (2)
        stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True,
        )

        numChannels = wf.getnchannels()
        sampleWidth = wf.getsampwidth()
        frameWidth = numChannels * sampleWidth
        wrapData: bytearray | None = None

        # Play samples from the wave file (3)
        while len(data := wf.readframes(CHUNK)):  # Requires Python 3.8+ for :=
            (shiftedData, wrapData) = frameShift(data, wrapData, frameWidth, sampleWidth)
            stream.write(bytes(shiftedData))

        # Close stream (4)
        stream.close()

        # Release PortAudio system resources (5)
        p.terminate()


def frameShift(data: bytes, wrapData: bytearray | None, frameWidth: int, sampleWidth: int):
    writeableData = bytearray(data)
    dataLen = len(data)
    numFrames = int(dataLen / frameWidth)

    lastWrapData = wrapData
    wrapData = bytearray([0 for _ in range(FRAME_SHIFT * frameWidth)])

    for iFrame in range(numFrames - 1, -1, -1):
        srcStartByte = iFrame * frameWidth
        destStartByte = srcStartByte + FRAME_SHIFT * frameWidth

        for i in range(sampleWidth):
            if destStartByte < dataLen - 1:
                writeableData[destStartByte + i] = data[srcStartByte + i]
            else:
                wrapData[destStartByte - dataLen + i] = data[srcStartByte + i]

    for iWrapFrame in range(FRAME_SHIFT - 1, -1, -1):
        startByte = iWrapFrame * frameWidth

        for i in range(sampleWidth):
            writeableData[startByte + i] = lastWrapData[srcStartByte + i] if lastWrapData else 0

    return (writeableData, wrapData)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Plays a wave file. Usage: {sys.argv[0]} filename.wav")
        sys.exit(-1)

    # frameWidth = 4
    # sampleWidth = 2
    # testData = bytes([x for x in range(256)])
    # (shiftedData, wrapData) = frameShift(testData, None, frameWidth, sampleWidth)

    playWithShift(sys.argv[1])
