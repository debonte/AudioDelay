import wave
import sys

import pyaudio


CHUNK = 1024*6
FRAME_SHIFT = 1024*32


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
            (shiftedData, wrapData) = shift(data, wrapData, frameWidth, sampleWidth, FRAME_SHIFT)
            stream.write(bytes(shiftedData))

        # Close stream (4)
        stream.close()

        # Release PortAudio system resources (5)
        p.terminate()


def shift(data: bytes, wrapData: bytearray | None, frameWidth: int, sampleWidth: int, frameShift: int):
    writeableData = bytearray(data)
    dataLen = len(data)
    numFrames = int(dataLen / frameWidth)

    lastWrapData = wrapData
    wrapData = bytearray([0 for _ in range(frameShift * frameWidth)])
    if lastWrapData and dataLen < len(lastWrapData):
        for i in range(len(lastWrapData) - dataLen):
            wrapData[i] = lastWrapData[i + dataLen]

    for iFrame in range(numFrames - 1, -1, -1):
        srcStartByte = iFrame * frameWidth
        destStartByte = srcStartByte + frameShift * frameWidth

        for i in range(sampleWidth):
            if destStartByte < dataLen - 1:
                writeableData[destStartByte + i] = data[srcStartByte + i]
            else:
                wrapData[destStartByte - dataLen + i] = data[srcStartByte + i]

    for iWrapFrame in range(min(frameShift, numFrames) - 1, -1, -1):
        startByte = iWrapFrame * frameWidth

        for i in range(sampleWidth):
            writeableData[startByte + i] = lastWrapData[startByte + i] if lastWrapData else 0

    return (writeableData, wrapData)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Plays a wave file. Usage: {sys.argv[0]} filename.wav")
        sys.exit(-1)

    # frameWidth = 4
    # sampleWidth = 2
    # testData = [x for x in range(64)]
    # chunkSize = 4
    # startOffset = 0
    # frameShift = 2
    # wrapData = None

    # print(*testData)
    # while startOffset < len(testData):
    #     (shiftedData, wrapData) = shift(bytes(testData[startOffset:startOffset + chunkSize]), wrapData, frameWidth, sampleWidth, frameShift)
    #     startOffset = startOffset + chunkSize
    #     print(list(shiftedData))


    # print("Done")
    playWithShift(sys.argv[1])
