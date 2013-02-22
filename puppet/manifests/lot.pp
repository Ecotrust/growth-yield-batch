# ensure that apt update is run before any packages are installed
class apt {
  exec { "apt-update":
    command => "/usr/bin/apt-get update"
  }

  # Ensure apt-get update has been run before installing any packages
  Exec["apt-update"] -> Package <| |>

}

include apt

package { "build-essential":
    ensure => "installed"
}

package { "python-software-properties":
    ensure => "installed"
}

package { "git-core":
    ensure => "latest"
}

package { "vim":
    ensure => "latest"
}

package { "python-psycopg2":
    ensure => "latest"
}

package { "python-virtualenv":
    ensure => "latest"
}

package { "python-dev":
    ensure => "latest"
}

package { "redis-server":
    ensure => "latest"
}

package {'supervisor':
    ensure => "latest"
}

class { "postgresql::server": version => "9.1",
    listen_addresses => 'localhost',
    max_connections => 100,
    shared_buffers => '24MB',
}

postgresql::database { "forestplanner":
  owner => "vagrant",
}

file { "go":
  path => "/home/vagrant/go",
  content => template("go"),
  owner => "vagrant",
  group => "vagrant",
  mode => 0775
}

file { "celeryd.conf":
  path => "/etc/supervisor/conf.d/celeryd.conf",
  content => template("celeryd.conf")
}

class { "celery::server":
  requirements => "/vagrant/requirements.txt"
}

# preferred symlink syntax
file { '/var/celery/tasks.py':
   ensure => 'link',
   target => '/usr/local/apps/land_owner_tools/scripts/tasks.py',
}