
def calc_days(rx, cond, site, clim, offsets, cpus=1, calib_keys=80, calib_sec=314):
    keys = rx * cond * site * clim * offsets
    # 80 keys took 303 sec
    seconds = (keys / float(calib_keys)) * calib_sec
    days = seconds / 60 / 60 / 24 / cpus
    return days

if __name__ == "__main__":
    print calc_days(rx=37, cond=18000, site=1, clim=13, offsets=5, cpus=32)
