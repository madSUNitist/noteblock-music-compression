mod sia;
mod tec;
mod siatec;
mod cosiatec;
mod recursia;

use pyo3::prelude::*;

#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sia::find_mtps, m)?)?;
    m.add_function(wrap_pyfunction!(siatec::build_tecs_from_mtps, m)?)?;
    m.add_function(wrap_pyfunction!(cosiatec::cosiatec_compress, m)?)?;
    m.add_function(wrap_pyfunction!(recursia::recursive_cosiatec_compress, m)?)?;
    m.add_function(wrap_pyfunction!(tec::is_better_tec, m)?)?;
    m.add_class::<tec::TranslationalEquivalence>()?;
    Ok(())
}