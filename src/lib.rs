mod sia;
mod tec;
mod siatec;
mod cosiatec;
mod recursia;

use pyo3::prelude::*;

#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sia::sia, m)?)?;
    m.add_function(wrap_pyfunction!(siatec::siatec, m)?)?;
    m.add_function(wrap_pyfunction!(cosiatec::cosiatec, m)?)?;
    m.add_function(wrap_pyfunction!(cosiatec::compress_to_encoding, m)?)?;
    m.add_function(wrap_pyfunction!(siatec::is_better_tec, m)?)?;
    m.add_function(wrap_pyfunction!(recursia::recur_sia_cosiatec, m)?)?;
    m.add_class::<tec::TEC>()?;
    Ok(())
}