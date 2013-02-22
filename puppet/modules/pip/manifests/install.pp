define pip::install($cwd="/",
               $requirements="",
               $index="",
               $extra_index="",
               $timeout="") {
  if ($index != "") {
    $index_opt = "-i $index"
  } else {
    $index_opt = ""
  }

  if ($extra_index != "") {
    $extra_index_opt = "--extra-index $extra_index"
  } else {
    $extra_index_opt = ""
  }

  if ($requirements != "") {
    $to_install = "-r $requirements"
  } else {
    $to_install = "$name"
  }

  if ($timeout != "") {
    $timeout_opt = "--timeout=$timeout"
  } else {
    $timeout_opt = ""
  }
  exec { "pip-$name":
    # TODO --upgrade?
    command => "/usr/bin/pip install --use-mirrors $to_install $index_opt $extra_index_opt $timeout_opt",
    cwd => $cwd,
    user => $run_as_user,
    timeout => 0,
  }
}
