from nbs_compression.sia_family import recur_sia_cosiatec
from nbs_compression.sia_family import cosiatec
from nbs_compression.utils import notes_to_points, tecs_to_nbs

import pynbs

if __name__ == "__main__":
    nbs_file_path = 'nbs_files/test_9.nbs'

    # 1.1. Read `.nbs` file
    song = pynbs.read(nbs_file_path)
    raw_notes = [(tick, note.key, note.instrument) for tick, chord in song for note in chord] # Original note list: (tick, key, instrument)
    
    # 1.2. Convert into `Point`
    points = notes_to_points(raw_notes)
    
    # 2. Compress
    # tecs = cosiatec(points, restrict_dpitch_zero=True)
    tecs = recur_sia_cosiatec(points, restrict_dpitch_zero=True, min_pattern_size=2)

    # tecs = list(filter(lambda tec: len(tec.pattern) >= 10 or len(tec.translators) >= 10, tecs))
    
    # 3. Check results 
    print("RecurSIA result:")
    
    for i, tec in enumerate(tecs):
        print(f"TEC {i+1}: pattern={tec.pattern}, translators={tec.translators}")
        print(f"  Coverage count: {len(tec.coverage)}")
        print(f"  Compression ratio: {tec.compression_ratio:.3f}")
    
    # Calculate overall compression ratio
    original_count = len(raw_notes)
    encoded_patterns = sum(len(tec.pattern) for tec in tecs)
    encoded_translators = sum(len(tec.translators) for tec in tecs)
    encoded_units = encoded_patterns + encoded_translators
    overall_ratio = original_count / encoded_units if encoded_units > 0 else 0
    print(f"\nOverall compression ratio: {overall_ratio:.3f} (Original notes: {original_count}, Encoded units: {encoded_units} = {encoded_patterns} + {encoded_translators})")

    # 4. Rebuild & Write Back
    new_file = tecs_to_nbs(tecs, song.header.__dict__)
    new_file.save('.'.join(nbs_file_path.split('.')[:-1]) + '_rebuild.nbs')