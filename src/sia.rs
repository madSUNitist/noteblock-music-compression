use pyo3::prelude::*;

/// Run the SIA (Sequential Interactive Algorithm) to find all maximal translatable patterns.
/// 
/// # Arguments
/// * `dataset` - A list of points, each as a tuple `(tick, pitch)`.
/// * `restrict_dpitch_zero` - If true, only consider vectors with zero pitch difference.
/// 
/// # Returns
/// A vector of `(vector, start_points)` where `vector` is `(dtick, dpitch)`
/// and `start_points` is a sorted list of points that form the pattern.
#[pyfunction]
pub fn sia(dataset: Vec<(i64, i64)>, restrict_dpitch_zero: bool) -> Vec<((i64, i64), Vec<(i64, i64)>)> {
    let mut points = dataset;
    points.sort(); // lexicographic by (tick, pitch)
    let n = points.len();

    // Build vector table: for each pair (i, j) with i != j, store (vector, start_point)
    let mut vectors: Vec<((i64, i64), (i64, i64))> = Vec::with_capacity(n * n.saturating_sub(1));
    for i in 0..n {
        let (ti, pi) = points[i];
        for j in 0..n {
            if i == j {
                continue;
            }
            let (tj, pj) = points[j];
            let dx = ti - tj;
            let dy = pi - pj;
            if restrict_dpitch_zero && dy != 0 {
                continue;
            }
            vectors.push(((dx, dy), (tj, pj)));
        }
    }

    // Sort by vector (and then by start_point to get deterministic order)
    vectors.sort();

    // Group by vector and collect unique start points
    let mut result = Vec::new();
    let mut i = 0;
    let len = vectors.len();
    while i < len {
        let cur_vec = vectors[i].0;
        let mut start_pts = Vec::new();
        while i < len && vectors[i].0 == cur_vec {
            start_pts.push(vectors[i].1);
            i += 1;
        }
        if cur_vec == (0, 0) {
            continue;
        }
        // Remove duplicates and sort to match Python's `sorted(set(start_points))`
        start_pts.sort();
        start_pts.dedup();
        if start_pts.len() >= 2 {
            result.push((cur_vec, start_pts));
        }
    }
    result
}