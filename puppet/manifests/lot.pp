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

package {'wine':
    ensure => "latest",
    # require => Package['xvfb'],
}

# package {'xvfb':
#     ensure => "latest"
# }

# exec { "winecfg":
#   command => "/usr/bin/wineconsole --backend=curses",  # just run this to ensure ~/.wine cfg creation
#   user => "vagrant",
#   require => Package['wine'],
# }

# class { "postgresql::server": version => "9.1",
#     listen_addresses => 'localhost',
#     max_connections => 100,
#     shared_buffers => '24MB',
# }

# postgresql::database { "forestplanner":
#   owner => "vagrant",
# }

class { "celery::server":
  requirements => "/vagrant/requirements.txt"
}

# preferred symlink syntax
file { '/var/celery/tasks.py':
   ensure => 'link',
   target => '/usr/local/apps/growth-yield-batch/scripts/tasks.py',
}

file { "/usr/local/apps/growth-yield-batch/fvsbin/FVSpn.exe":
    ensure => "present",
}