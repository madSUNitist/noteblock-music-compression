from nbslim.sia_family import recursive_cosiatec_compress, recursive_cosiatec_compress_py
from nbslim.sia_family import cosiatec_compress, cosiatec_compress_py
from nbslim.sia_family import TranslationalEquivalence

from nbslim.utils import notes_to_points, tecs_to_nbs, compression_stats, merge_tecs

import pynbs

if __name__ == "__main__":
    nbs_file_path = 'nbs_files/青石巷.nbs'

    # 1. Read `.nbs` file & convert into `Point` & get mapping dict
    song = pynbs.read(nbs_file_path)
    points, note_dict = notes_to_points(song.notes)
    
    # 2. Compress
    # tecs = cosiatec_compress(points, restrict_dpitch_zero=True)
    tecs = recursive_cosiatec_compress(points, restrict_dpitch_zero=True, min_pattern_size=2)
    
    # 3. Check results 
    print("Result:")
    for i, tec in enumerate(tecs):
        print('TEC %d' % i)
        print(tec)
        print(tec.summary(indent=2))
    print()
    
    stats = compression_stats(tecs, points)
    print(f"Overall compression ratio: {stats['compression_ratio']:.3f} " 
          f"(Original: {stats['original_count']}, Encoded units: {stats['encoded_units']})")

    # 4. Rebuild & Write Back
    merged_tecs = merge_tecs(tecs) # Optioanl: Merge all TECs with coverage size <= 10 into one
    new_file = tecs_to_nbs(merged_tecs, note_dict, song.header.__dict__)
    new_file.save('.'.join(nbs_file_path.split('.')[:-1]) + '_rebuild.nbs')