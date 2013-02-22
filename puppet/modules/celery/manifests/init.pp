class celery::server($requirements="/tmp/celery-requirements.txt",
                     $requirements_template="celery/requirements.txt",
                     $initd_template="celery/init.d.sh",
                     $config_template="celery/celeryconfig.py",
                     $defaults_template="celery/defaults.sh",
                     $redis_broker_db="0",
                     $redis_results_db="0",
                     $redis_vis_timeout="43200",
                     $broker_host="localhost",
                     $broker_port="6379") {

  file { $requirements:
    ensure => "present",
  }

  pip::install {"celery":
    requirements => $requirements,
    require => [File[$requirements],],
  }

  file { "/etc/default/celeryd":
    ensure => "present",
    content => template($defaults_template),
    notify  => Service["celeryd"],
  }

  file { "/etc/init.d/celeryd":
    ensure => "present",
    content => template($initd_template),
    notify  => Service["celeryd"],
    mode => "0755",
  }

  user { "celery":
    ensure => "present",
  }

  file { "/var/celery":
    ensure => "directory",
    owner => "celery",
    require => User["celery"],
  }

  file { "/var/celery/celeryconfig.py":
    ensure => "present",
    content => template($config_template),
    require => File["/var/celery"],
    notify  => Service["celeryd"],
  }

  file { "/var/log/celery":
    ensure => "directory",
    owner => "celery",
  }

  file { "/var/run/celery":
    ensure => "directory",
    owner => "celery",
  }

  service { "celeryd":
    ensure => "running",
    enable  => "true",
    require => [File["/var/celery/celeryconfig.py"],
                File["/etc/init.d/celeryd"],
                Exec["pip-celery"],
                File["/var/log/celery"],
                File["/var/run/celery"],
                Package["redis-server"],
                ],
  }
}
