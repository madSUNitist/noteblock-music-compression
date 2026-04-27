use pyo3::prelude::*;
use std::collections::HashSet;

/// Translational Equivalence Class: a pattern + set of non-zero translators.
#[pyclass]
#[derive(Clone)]
pub struct TEC {
    /// Sorted pattern points
    #[pyo3(get)]
    pub pattern: Vec<(i64, i64)>,
    /// Non-zero translators
    #[pyo3(get)]
    pub translators: HashSet<(i64, i64)>,
    /// Sub-TECs (optional)
    #[pyo3(get)]
    pub sub_tecs: Vec<TEC>,
}

#[pymethods]
impl TEC {
    #[new]
    pub fn new(
        pattern: Vec<(i64, i64)>,
        translators: HashSet<(i64, i64)>,
        sub_tecs: Option<Vec<TEC>>,
    ) -> Self {
        let mut pattern_sorted = pattern;
        pattern_sorted.sort();
        TEC {
            pattern: pattern_sorted,
            translators,
            sub_tecs: sub_tecs.unwrap_or_else(Vec::new),
        }
    }

    /// Covered set = pattern ∪ all translated copies.
    #[getter]
    pub fn coverage(&self, _py: Python) -> PyResult<HashSet<(i64, i64)>> {
        let mut cov = HashSet::new();
        for &p in &self.pattern {
            cov.insert(p);
        }
        for &v in &self.translators {
            for &p in &self.pattern {
                cov.insert((p.0 + v.0, p.1 + v.1));
            }
        }
        Ok(cov)
    }

    /// Compression ratio = |covered set| / (|pattern| + |translators|).
    #[getter]
    pub fn compression_ratio(&self, py: Python) -> PyResult<f64> {
        let covered_len = self.coverage(py)?.len() as f64;
        let pattern_len = self.pattern.len() as f64;
        let trans_len = self.translators.len() as f64;
        let denom = pattern_len + trans_len;
        if denom == 0.0 {
            Ok(0.0)
        } else {
            Ok(covered_len / denom)
        }
    }

    /// Bounding‑box compactness: |pattern| / (number of dataset points inside pattern's bbox).
    pub fn compactness(&self, points: HashSet<(i64, i64)>) -> f64 {
        if self.pattern.is_empty() {
            return 0.0;
        }
        let xs: Vec<i64> = self.pattern.iter().map(|p| p.0).collect();
        let ys: Vec<i64> = self.pattern.iter().map(|p| p.1).collect();
        let min_x = *xs.iter().min().unwrap();
        let max_x = *xs.iter().max().unwrap();
        let min_y = *ys.iter().min().unwrap();
        let max_y = *ys.iter().max().unwrap();
        let mut count = 0;
        for &(x, y) in &points {
            if x >= min_x && x <= max_x && y >= min_y && y <= max_y {
                count += 1;
            }
        }
        if count == 0 {
            0.0
        } else {
            self.pattern.len() as f64 / count as f64
        }
    }

    pub fn __repr__(&self) -> String {
        format!(
            "TEC(pattern={:?}, translators={:?})",
            self.pattern, self.translators
        )
    }
}