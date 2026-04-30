REM Following lines format: cdo "commands" input.nc > ..\output.txt
cdo -outputtab,date,value -fldmean -sellonlatbox,1.00,1.75,45.50,46.00 pre.nc > ..\pre_data.txt
cdo -outputtab,date,value -fldmean -sellonlatbox,1.00,1.75,45.50,46.00 pet.nc > ..\pet_data.txt
cdo -outputtab,date,value -fldmean -sellonlatbox,1.00,1.75,45.50,46.00 tavg.nc > ..\tavg_data.txt


REM Following line is for the q data obtained from GRDC in NetCDF format. Since GRDC data is already clipped, there is no need to apply a sellonlatbox command.
cdo -outputtab,date,value -fldmean -selname,runoff_mean q.nc > ..\q_data.txt

pause