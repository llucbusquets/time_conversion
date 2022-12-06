def time_conversion(folder_name):
    """
    This function reads a dat file with an array of dates in JD format and writes other dat files with the same dates
        coverted to UT1 in J2000, UT1 in MJD, UTC in J2000 and GPS in J2000. The input file must have the name
        't_jd.dat' and must be located in a subfolder whose name is provided as input. This function retrieves the time
        conversion tables in their most current version from the US Navy website, hence works for converting jd times
        within +-90 days of the current date.
    :param folder_name: str - name of the subfolder in the currend directory where the JD array is saved and where all
        results will be saved
    :return: N/A
    """

    jd_array = np.loadtxt(folder_name + '\\t_jd.dat')

    url = "https://maia.usno.navy.mil/ser7/finals2000A.daily"
    print("Retrieving IAU2000A UT1-UTC conversion table...")
    data = requests.get(url)
    table_UT1_UTC = data.text.splitlines()
    nrows = len(table_UT1_UTC)

    MJD_column = np.zeros(nrows)
    UT1_UTC_column = np.zeros(nrows)
    for i in range(nrows):
        row = table_UT1_UTC[i]
        MJD_column[i] = float(row[7:15])
        UT1_UTC_column[i] = float(row[58:68])
    url = "https://maia.usno.navy.mil/ser7/tai-utc.dat"
    print("Retrieving IERS TAI-UTC leap seconds table...")
    data = requests.get(url)
    table_TAI_UTC = data.text.splitlines()
    nrows = len(table_TAI_UTC)

    JD_column = np.zeros(nrows)
    leap_sec_column = np.zeros(nrows)
    for i in range(nrows):
        row = table_TAI_UTC[i]
        JD_column[i] = float(row[17:27])
        leap_sec_column[i] = float(row[38:43])

    nsteps = len(jd_array)
    UT1_J2000 = np.zeros(nsteps)
    UT1_MJD = np.zeros(nsteps)
    GPS_J2000 = np.zeros(nsteps)
    UTC_J2000 = np.zeros(nsteps)
    for i in range(nsteps):
        JD = jd_array[i]
        MJD = jd2mjd(JD)
        JD_J2000 = JD - 2451545.0
        UTC_J2000[i] = JD_J2000*86400

        j = int(np.where(MJD_column == (np.floor(MJD)))[0])
        delta_i = UT1_UTC_column[j]
        delta_s = UT1_UTC_column[j+1]
        MJD_i = MJD_column[j]
        MJD_s = MJD_column[j+1]
        delta = delta_i + (delta_s - delta_i)/(MJD_s-MJD_i)*(MJD-MJD_i)
        UT1_J2000[i] = UTC_J2000[i] + delta
        UT1_MJD[i] = UT1_J2000[i]/86400 + 2451545.0 - 2400000.5

        j = 0
        while JD_column[j] - JD < 0 and j < nrows - 1:
            j = j + 1

        delta = leap_sec_column[j]
        GPS_J2000[i] = UTC_J2000[i] - (delta - 19.0)    # At January 6th 1980 00:00: (JD 2444244.50000), TAI-UTC was 19s

    print("Saving converted time arrays...")
    np.savetxt(folder_name + '\\t_UT1J2000.dat', UT1_J2000, fmt='%.11e')
    np.savetxt(folder_name + '\\t_GPSJ2000.dat', GPS_J2000, fmt='%.11e')
    np.savetxt(folder_name + '\\t_UTCJ2000.dat', UTC_J2000, fmt='%.11e')
    np.savetxt(folder_name + '\\t_UT1MJD.dat', UT1_MJD, fmt='%.11e')