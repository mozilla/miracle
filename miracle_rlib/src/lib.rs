#[macro_use] extern crate cpython;
extern crate url;

use cpython::{exc, PyResult, Python, PyErr, PyUnicode, ToPyObject, PythonObject};
use url::{Url, ParseError};


py_module_initializer!(libmiracle_rlib, initlibmiracle_rlib,
                       PyInit_libmiracle_rlib, |py, m| {
    try!(m.add(py, "__doc__", "Miracle Rust library."));
    try!(m.add(py, "url_parse", py_fn!(py, url_parse_py(input: &str))));
    try!(m.add(py, "add_int", py_fn!(py, add_int(a: i64, b: i64))));
    Ok(())
});


fn url_parse_py(py: Python, input: &str) -> PyResult<PyUnicode> {
    match url_parse(input) {
        Ok(n) => {
            match n {
                None => Ok(PyUnicode::new(py, "")),
                Some(n) => Ok(PyUnicode::new(py, &n)),
            }
        },
        Err(err) => {
            let msg = "ParseError";
            let pyerr = PyErr::new_lazy_init(
                py.get_type::<exc::ValueError>(),
                Some(msg.to_py_object(py).into_object())
            );
            Err(pyerr)
        },
    }
}


fn url_parse(input: &str) -> Result<Option<String>, ParseError> {
    let url = Url::parse(input)?;
    let host = url.host_str().unwrap_or("").to_owned();
    Ok(Some(host))
}


fn add_int(py: Python, a: i64, b: i64) -> PyResult<i64> {
    Ok(a + b)
}
