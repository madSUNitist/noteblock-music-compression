from nbs_compression.sia_family.recursia import recur_sia_cosiatec
from nbs_compression.sia_family.cosiatec import cosiatec
from nbs_compression.utils import notes_to_points, visualize, rebuild

import pynbs

if __name__ == "__main__":
    nbs_file_path = 'nbs_files/STAY.nbs'

    # 1.1. Read `.nbs` file
    song = pynbs.read(nbs_file_path)
    raw_notes = [(tick, note.key, note.instrument) for tick, chord in song for note in chord] # Original note list: (tick, key, instrument)
    
    # 1.2. Convert into `Point`
    points = notes_to_points(raw_notes)
    
    # 2. Compress
    tecs = recur_sia_cosiatec(points, restrict_dpitch_zero=True, min_pattern_size=5)

    # tecs = list(filter(lambda tec: len(tec.pattern) >= 10 or len(tec.translators) >= 10, tecs))
    
    # 3. Check results 
    print("RecurSIA result:")
    
    for i, tec in enumerate(tecs):
        print(f"TEC {i+1}: pattern={tec.pattern}, translators={tec.translators}")
        print(f"  Coverage count: {len(tec.coverage)}")
        print(f"  Compression ratio: {tec.compression_ratio:.3f}")

    
    # 4. Visualize
    visualize(tecs)
    
    # 5. Rebuild & Write Back
    rebuilt_points = rebuild(tecs)

    new_file = pynbs.new_file(**song.header.__dict__)

    curr_tick, curr_layer = -1, 0
    for point in rebuilt_points:
        tick, key = point.tick, point.key
        for inst in point.inst_set:
            # update curr_tick & curr_layer
            if curr_tick != tick:
                curr_tick, curr_layer = tick, 0
            else:
                curr_layer += 1
            
            # add note
            new_file.notes.append(
                pynbs.Note(tick, curr_layer, inst, key)
            )

    new_file.save('.'.join(nbs_file_path.split('.')[:-1]) + '_rebuild.nbs')