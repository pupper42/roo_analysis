# Example of the use of the SP3 package

use PDL;
use SP3;

my $infile = "test_gps_orb.sp3";  # SP3 file to read in

my ($times, $pos, $options, $vel) = SP3::readSP3 ($infile);

# At this point: 
# -- $times contains a 1D PDL (array) of times of orbit positions/velocities 
#    in GPS second.  
# -- $pos contains a 3D PDL of positions indexed by time step (matching the
#    $times vector), XYZ and GPS satellite ID (PRN number).  
# -- $options contains a reference to
#     a perl hash with some information read in from the SP3 header.  
# -- $vel is similar to $pos, but contains velocity data.

# The location of the KOKEE park ground station
my $kokee_park = pdl (-5543.8069, -2054.589748, 2387.875707);

# Use the 'slice' function to pull out sections of a PDL.
# The (3) selects the third dimension and reduces the dimensionality of the PDL
# from 3 to 2.  'xchg' swaps the dimensions of sat_pos_3 in
# preparation for the next operation.
my $sat_pos_3  = $pos->slice(":,:,(3)")->xchg(0,1);

# Distance in km from the station to the GPS satellite at each time step.
my $range = sqrt(sumover(($sat_pos_3 - $kokee_park)**2));

print $range;

print "Done!\n";
