define pip::bootstrap() {
  package { "curl" :
    ensure => "latest",
  }

  exec { "distribute::bootstrapped":
    command => "curl http://python-distribute.org/distribute_setup.py | python",
    require => Package["curl"],
    onlyif => "python -c 'import sys
try:
  import setuptools;
except ImportError:
  sys.exit(0)
sys.exit(1)'",
  }

  exec { "pip::bootstrapped":
    command => "curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python",
    require => Exec["distribute::bootstrapped"],
    onlyif => "bash -c 'which pip > /dev/null && exit 1 || exit 0'",
  }
}
