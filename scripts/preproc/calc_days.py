
def calc_days(rx, cond, site, clim, offs, cpus=1, calib_keys=80, calib_sec=303):
    keys = rx * cond * site * clim * offs
    # 80 keys took 303 sec
    seconds = (keys / float(calib_keys)) * calib_sec
    days = seconds / 60 / 60 / 24 / cpus
    return days

if __name__ == "__main__":
    print calc_days(37, 18000, 1, 13, 5, 32)
