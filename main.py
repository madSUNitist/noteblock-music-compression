from nbs_compression.sia_family.recursia import recur_sia_cosiatec
# from nbs_compression.sia_family.cosiatec import cosiatec
import pynbs

if __name__ == "__main__":
    nbs_file_path = 'nbs_files/test.nbs'

    notes = []
    for tick, chord in pynbs.read(nbs_file_path):
        for note in chord:
            notes.append((tick, note.key))

    tecs = recur_sia_cosiatec(notes, restrict_dpitch_zero=True)
    print("RecurSIA result:")
    
    # tecs = cosiatec(notes, restrict_dpitch_zero=True)
    # print("COSIATEC result:")
    
    for i, tec in enumerate(tecs):
        print(f"TEC {i+1}: pattern={tec.pattern}, translators={tec.translators}")
        print(f"  Coverage count: {len(tec.coverage)}")
        print(f"  Compression ratio: {tec.compression_ratio:.3f}")
    # print("\nCompressed encoding:")
    # encoding = compress_to_encoding(tecs)
    # print(encoding)