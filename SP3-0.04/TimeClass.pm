#!/bin/perl -w
#/**----------------------------------------------------------------------    
# @name       TimeClass.pm
#
# Class for dealing with GPS times in various representations
#
# Typically, one creates a new TimeClass object, initializes it, and
# then performs a conversion and extracts the result.  This can be done
# all on one line, like this:
#
# $gpssec = 500000000;
# my ($gpswk, $gpsday) = TimeClass->new->set_gps ($gpssec)->get_gpswk_day;
#  
# @author     Chris Bogart, Doug Hunt
# @since      08/29/96
# @version    $Revision: 1.13 $
# -----------------------------------------------------------------------*/
use lib qw(. /ops/tools/lib);
use strict;
use Time::Local;
use Carp;

package TimeClass;

#---------------------------------------------------------------------------
## Global variables
#---------------------------------------------------------------------------

# number of seconds between unix time base (1970)
# and gps time base (jan 6, 1980).  This neglects
# the growing leap second offset (now 11 seconds)
$TimeClass::GPSSEC = 315964800;


#/**----------------------------------------------------------------------    
# @name       new
# 
# Create a new TimeClass object
# 
# @parameter  type      Type of object (normally 'TimeClass' unless subclassed)
# @return     A blessed TimeClass object
# @example    my $tc = TimeClass->new;
# ----------------------------------------------------------------------*/
sub new
{
    my $type = shift;
    my $self = {};
    bless $self, $type;
    return $self;
}


#/**----------------------------------------------------------------------    
# @name       set_gps
# 
# Create a new TimeClass object
# 
# @parameter  self     a TimeClass object
# @           gps_time The GPS time in seconds
# @return     self     a TimeClass object
# ----------------------------------------------------------------------*/
sub set_gps
{
    my $self = shift;
    $self->_reset;
    $self->{"gps"} = int(shift);
    return $self;
}


#/**----------------------------------------------------------------------    
# @name       set
# 
# Set from another time object
# 
# @parameter  set_to   a TimeClass object
# @           set_from a TimeClass object
# @return     new      a TimeClass object
# ----------------------------------------------------------------------*/
sub set { %{$_[0]} = %{$_[1]}; $_[0]; }


#/**----------------------------------------------------------------------    
# @name       set_j2000
# 
# Set j2000 time
# 
# @parameter  self     a TimeClass object
# @           j2000 time in seconds
# @return     self     a TimeClass object
# ----------------------------------------------------------------------*/
sub set_j2000
{
   my $self = shift;
   $self->_reset;
   $self->{"gps"} = int(shift) + 630763200;
   $self;
}


#/**----------------------------------------------------------------------    
# @name       get_j2000
# 
# Get j2000 time
# 
# @parameter  self     a TimeClass object
# @return     j2000 time, seconds
# ----------------------------------------------------------------------*/
sub get_j2000
{
   my $self = shift;
   return $self->get_gps - 630763200;
}


#/**----------------------------------------------------------------------    
# @name       set_julian
# 
# Set Julian Date
# 
# @parameter  self     a TimeClass object
# @           julian date in days
# @return     self     a TimeClass object
# ----------------------------------------------------------------------*/
sub set_julian
{
   my $self = shift;
   $self->_reset;
   my $julian = shift;
   $self->set_j2000(0);
   $self->inc_sec_gps( ($julian - 2451545.0) * (3600.0 * 24) );
   $self;
}

#/**----------------------------------------------------------------------    
# @name       get_julian
# 
# Get Julian Date
# 
# @parameter  self     a TimeClass object
# @return     julian time, days
# ----------------------------------------------------------------------*/
sub get_julian
{
   my $self = shift;
   return ($self->get_j2000 / (3600*24.0) + 2451545);
}


#/**----------------------------------------------------------------------    
# @name       set_tai93
# 
# Set TAI93 time
# 
# @parameter  self     a TimeClass object
# @           tai93 time in seconds (Seconds since 1/1/1993)
# @return     self     a TimeClass object
# ----------------------------------------------------------------------*/
sub set_tai93
{
   my $self = shift;
   $self->_reset;
   $self->{"gps"} = int(shift) + 409881608;
   $self;
}


#/**----------------------------------------------------------------------    
# @name       get_tai93
# 
# Get TAI93 time
# 
# @parameter  self     a TimeClass object
# @return     Seconds since 1/1/1993
# ----------------------------------------------------------------------*/
sub get_tai93
{
   my $self = shift;
   return $self->get_gps - 409881608;   # Seconds since 1/1/1993
}


#/**----------------------------------------------------------------------    
# @name       set_uars
# 
# Set time from UARS day number (day 1.0 = Sept 12, 1991 at midnight UTC)
# 
# @parameter  self     a TimeClass object
# @           UARS day number (need not be an integer)
# @return     self     a TimeClass object
# ----------------------------------------------------------------------*/
sub set_uars
{
  my ($self, $uarsday) = @_;
  $self->_reset;
  $self->{"gps"} = 368668800 + (86400 * $uarsday);
  return $self;
}


#/**----------------------------------------------------------------------    
# @name       get_gps
# 
# Return gps seconds
# 
# @parameter  self     a TimeClass object
# @return     gps seconds since 1/6/1980
# ----------------------------------------------------------------------*/
sub get_gps
{
    my $self = shift;
    return $self->{"gps"} if (exists $self->{"gps"});
    die "Time not set";
}


#/**----------------------------------------------------------------------    
# @name       get_gpsweek_day
# 
# Return gps week and day
# 
# @parameter  self     a TimeClass object
# @return     gps week
# @           gps day
# ----------------------------------------------------------------------*/
sub get_gpsweek_day
{
    my $self = shift;
    $self->get_gps;
    my $week = int($self->{"gps"} / (7 * 24 * 3600) );
    my $day = int(($self->{"gps"} - ($week * 7 * 24 * 3600)) / (24 * 3600));
    return ($week, $day);
}


#/**----------------------------------------------------------------------    
# @name       set_gpsweek_day
# 
# Set gps week and day
# 
# @parameter  self     a TimeClass object
# @           gps week
# @           gps day
# @return     self     a TimeClass object
# ----------------------------------------------------------------------*/
sub set_gpsweek_day
{
    my $self = shift;
    my $gpsweek = shift;
    my $gpsday = shift;

    die "Day must be between 0 and 6" if $gpsday > 6 || $gpsday < 0;

    $self->_reset;
    $self->{"gps"} = $gpsweek * 7 * 24 * 3600 + $gpsday * 24 * 3600;
    $self;
}


#/**----------------------------------------------------------------------    
# @name       get_compact_date_gps
# 
# Return GPS date in %02d/%02d/%02d %02d:%02d:%02d format
# 
# @parameter  self     a TimeClass object
# @return     GPS date string
# ----------------------------------------------------------------------*/
sub get_compact_date_gps
{
    my $self = shift;
    $self->_create_gps_breakdown;
    sprintf  "%02d/%02d/%02d %02d:%02d:%02d",
	$self->{"gps month"},
	$self->{"gps day"},
	two_digit_year($self->{"gps year"}),
	$self->{"gps hour"},
	$self->{"gps minute"},
	$self->{"gps second"};
}


#/**----------------------------------------------------------------------    
# @name       set_emp_gps
# 
# Set time from an empress format (YYYYMMDDHHMMSS) time string in GPS time
# 
# @parameter  self     a TimeClass object
# @           date/time string
# @return     self     a TimeClass object
# ----------------------------------------------------------------------*/
sub set_emp_gps 
{
    my ($self, $empgps) = @_;

    die "Illegal date: $empgps" if (length($empgps)<14);
    $self->_reset;
    $self->{"gps"} = Time::Local::timegm (
        substr($empgps, 12, 2),
        substr($empgps, 10, 2),
        substr($empgps, 8, 2),
        substr($empgps, 6, 2),
        substr($empgps, 4, 2)-1,
        substr($empgps, 0, 4)-1900) - $TimeClass::GPSSEC;
    return $self;
}


#/**----------------------------------------------------------------------    
# @name       get_emp_gps
# 
# Get time in empress format (YYYYMMDDHHMMSS) in GPS time system
# 
# @parameter  self     a TimeClass object
# @return     empress format (YYYYMMDDHHMMSS) time/date string
# ----------------------------------------------------------------------*/
sub get_emp_gps 
{
    my $self = shift;
    $self->_create_gps_breakdown;
    sprintf("%04d%02d%02d%02d%02d%02d",
        $self->{"gps year"},
        $self->{"gps month"},
        $self->{"gps day"},
        $self->{"gps hour"},
        $self->{"gps minute"},
        $self->{"gps second"});
}

#/**----------------------------------------------------------------------    
# @name       get_stamp_gps
# 
# Get time in COSMIC time stamp format (YYYY.DDD.HH.MM.SS) in GPS time system
# 
# @parameter  self     a TimeClass object
# @return     time stamp format (YYYY.DDD.HH.MM.SS) time/date string
# ----------------------------------------------------------------------*/
sub get_stamp_gps 
{
    my $self = shift;
    $self->_create_gps_breakdown;
    sprintf("%04d.%03d.%02d.%02d.%02d",
        $self->{"gps year"},
        $self->{"gps doy"},
        $self->{"gps hour"},
        $self->{"gps minute"},
        $self->{"gps second"});
}

#/**----------------------------------------------------------------------    
# @name    get_datestring_gps
# 
# Get GPS time date string
# 
# @parameter  self     a TimeClass object
# @return     local 'monthname day, year'
# ----------------------------------------------------------------------*/
sub get_datestring_gps 
{
    my $self = shift;

    my $retval = "";

    $retval = $self->get_monthname_gps;
    $retval .= " " . $self->{"gps day"} . ", ";
    $retval .= $self->{"gps year"};

    return $retval;
 
}

#/**----------------------------------------------------------------------    
# @name    get_timestring_gps
# 
# Get GPS time string 
# 
# @parameter  self     a TimeClass object
# @return     GPS time in HH:MM:SS format
# ----------------------------------------------------------------------*/
sub get_timestring_gps
{
    my $self = shift;

    $self->_create_gps_breakdown;
    sprintf(" %02d:%02d:%02d", $self->{"gps hour"} , 
                    $self->{"gps minute"},  $self->{"gps second"});
}


#/**----------------------------------------------------------------------    
# @name    get_datetimestring_gps
# 
# Get GPS time/date string 
# 
# @parameter  self     a TimeClass object
# @return     GPS time in Month Day, year HH:MM:SS format
# ----------------------------------------------------------------------*/
sub get_datetimestring_gps 
{
    my $self = shift;

    return ($self->get_datestring_gps . " " . $self->get_timestring_gps);
}


#/**----------------------------------------------------------------------    
# @name   inc_sec_gps
# 
# Increment seconds in gps time
# 
# @parameter  self     a TimeClass object
# @           increment in seconds, default = 1
# @return     self     Timeclass object with several seconds later time
# ----------------------------------------------------------------------*/
sub inc_sec_gps
{
    my $self = shift;
    my $increment = shift;
    $increment = 1 if ! defined $increment;
    $self->set_gps($self->get_gps + $increment);
    $self;
}


#/**----------------------------------------------------------------------    
# @name   get_year_gps
# 
# Get GPS year
# 
# @parameter  self     a TimeClass object
# @return     GPS year
# ----------------------------------------------------------------------*/
sub get_year_gps { 
    my $self = shift;
    $self->_create_gps_breakdown;
    return $self->{"gps year"};
}


#/**----------------------------------------------------------------------    
# @name   get_month_gps
# 
# Get GPS month
# 
# @parameter  self     a TimeClass object
# @return     GPS month
# ----------------------------------------------------------------------*/
sub get_month_gps 
{
    my $self = shift;
    $self->_create_gps_breakdown;
    return $self->{"gps month"};
}


#/**----------------------------------------------------------------------    
# @name   get_hour_gps
# 
# Get GPS hour
# 
# @parameter  self     a TimeClass object
# @return     GPS hour
# ----------------------------------------------------------------------*/
sub get_hour_gps
{
    my $self = shift;
    $self->_create_gps_breakdown;
    return $self->{"gps hour"};
}


%TimeClass::rev_monthnames =
    ( "Jan"=>1,
      "Feb"=>2,
      "Mar"=>3,
      "Apr"=>4,
      "May"=>5,
      "Jun"=>6,
      "Jul"=>7,
      "Aug"=>8,
      "Sep"=>9,
      "Oct"=>10,
      "Nov"=>11,
      "Dec"=>12 );

%TimeClass::monthnames =
    ( 1=>"Jan",
      2=>"Feb",
      3=>"Mar",
      4=>"Apr",
      5=>"May",
      6=>"Jun",
      7=>"Jul",
      8=>"Aug",
      9=>"Sep",
      10=>"Oct",
      11=>"Nov",
      12=>"Dec" );

#/**----------------------------------------------------------------------    
# @name get_monthname_gps
# 
# Get month name from number
# 
# @parameter  self     a TimeClass object
# @return     month name
# ----------------------------------------------------------------------*/
sub get_monthname_gps
{
    my $self = shift;
    return $TimeClass::monthnames{$self->get_month_gps};
}


#/**----------------------------------------------------------------------    
# @name  set_ymdhms_gps
# 
# Set GPS time from yr, mo, day, hr, min, sec
# 
# @parameter  self     a TimeClass object
# @           yr, mon, day, hr, min, sec
# @return     self
# ----------------------------------------------------------------------*/
sub set_ymdhms_gps
{
    my $self = shift;
    my ($yr, $mo, $dy, $hr, $mi, $se) = @_;

    $self->_reset;
    $self->{"gps"} = Time::Local::timegm($se, $mi, $hr, $dy, $mo-1, 
		three_digit_year($yr)) - $TimeClass::GPSSEC;
    return $self;
}

#/**----------------------------------------------------------------------    
# @name  set_yrdoy_gps
# 
# Set GPS time from 'YY.DDD' or 'YYYY.DDD'
# 
# @parameter  self     a TimeClass object
# @           string:  'YY.DDD' or 'YYYY.DDD'
# @return     self
# ----------------------------------------------------------------------*/
sub set_yrdoy_gps 
{
    my $self = shift;
    my $yrdoy = shift;

    $self->_reset;
    my ($yr, $doy)  = $yrdoy =~ /^(\d+)\.(\d+)$/; 
    my ($mo, $mday) = find_date ($yr, $doy);

    $self->{"gps"}  = 
      Time::Local::timegm(0,0,0, $mday, $mo-1, three_digit_year($yr)) - 
	$TimeClass::GPSSEC;
    return $self;
}

#/**----------------------------------------------------------------------    
# @name  set_yrdoyhms_gps
# 
# Set GPS time from yr, doy, hr, min, sec
# 
# @parameter  self     a TimeClass object
# @           string:  'YY.DDD' or 'YYYY.DDD'
# @return     self
# ----------------------------------------------------------------------*/
sub set_yrdoyhms_gps 
{
    my $self = shift;
    my ($yr, $doy, $hr, $min, $sec) = @_;

    $self->_reset;
    my ($mo, $mday) = find_date ($yr, $doy);

    $self->{"gps"}  = 
      Time::Local::timegm($sec, $min, $hr, $mday, $mo-1, three_digit_year($yr)) - 
	$TimeClass::GPSSEC;
    return $self;
}


#/**----------------------------------------------------------------------    
# @name  set_yrfrac_gps
# 
# Set GPS time from a year with a fractional part
# 
# @parameter  self     a TimeClass object
# @           yr       a floating point year (eg 1997.04544)
# @return     self
# ----------------------------------------------------------------------*/
sub set_yrfrac_gps {
    my $self = shift;
    my $yr   = shift; # includes fractional part

    $self->_reset;

    my $feb = 28;
    if    ($yr % 4   == 0) {$feb = 29;} 
    if    ($yr % 100 == 0) {$feb = 28;} 
    if    ($yr % 400 == 0) {$feb = 29;} 

    my $daysThisYear = 337 + $feb;
    
    my $doy = (($yr - int($yr)) * $daysThisYear) + 1;  # includes fractional part

    my ($mo, $mday) = find_date (int($yr), int($doy));

    my $hr  = ($doy - int($doy)) * 24; # includes fractional part
    my $min = ($hr  - int($hr))  * 60; # includes fractional part
    my $sec = ($min - int($min)) * 60; # includes fractional part

    $self->{"gps"}  = 
      Time::Local::timegm($sec, int($min), int($hr), $mday, $mo-1, three_digit_year(int($yr))) - 
	$TimeClass::GPSSEC;
    return $self;
}


#/**----------------------------------------------------------------------    
# @name  set_yrdoyfrac_gps
# 
# Set GPS time from a year and a day of year with a fractional part
# 
# @parameter  self     a TimeClass object
# @           yr       a year (eg 1997)
# @           doy      a day of year with a fractional part (eg 105.398383)
# @return     self
# ----------------------------------------------------------------------*/
sub set_yrdoyfrac_gps {
    my $self = shift;
    my $yr   = shift;
    my $doy  = shift; # includes fractional part

    $self->_reset;

    my ($mo, $mday) = find_date ($yr, int($doy));

    my $hr  = ($doy - int($doy)) * 24; # includes fractional part
    my $min = ($hr  - int($hr))  * 60; # includes fractional part
    my $sec = ($min - int($min)) * 60; # includes fractional part

    $self->{"gps"}  = 
      Time::Local::timegm($sec, int($min), int($hr), $mday, $mo-1, three_digit_year(int($yr))) - 
	$TimeClass::GPSSEC;
    return $self;
}


#/**----------------------------------------------------------------------    
# @name  get_yrdoy_gps
# 
# Get GPS time in 'YYYY.DDD' format
# 
# @parameter  self     a TimeClass object
# @return     YYYY.DDD
# ----------------------------------------------------------------------*/
sub get_yrdoy_gps
{
    my $self = shift;

    $self->_create_gps_breakdown;
    sprintf("%02d.%03d", four_digit_year($self->{"gps year"}), $self->{"gps doy"});
}


#/**----------------------------------------------------------------------    
# @name  four_digit_year
#
# Either output the four digit year of the object,
# or if there's an argument, consider it a year
# and convert to four digits -- regardless of whether
# the argument is a 2, 3, or 4 digit year.
#
# This will have to be
# rewritten in 2050 because it assumes 2-digit
# years are between 1968 and 2050.  I hope we're
# not still converting 2 to 4 digit years in 2050;
# haven't we learned anything from the Y2K snafu?
# Note to grandchildren: get a clue.
#
# @parameter  self     a TimeClass object
# @           (optional) year
# @return     YYYY
# ----------------------------------------------------------------------*/
sub four_digit_year
{
    my ($self, $arg) = @_;
    if (!defined $arg)
    {
        $arg = $self->get_year_gps if ref $self;
        $arg = $self if !ref $self;
    }
    return 1900 + $arg if $arg>68 && $arg<150;
    return 2000 + $arg if $arg<51 and $arg > -1;
    return $arg if $arg < 2050 && $arg > 1968;
    die "$arg -- unknown year";
}


#/**----------------------------------------------------------------------    
# @name  get_mjd
#
#  Get Modified Julian Day (based on gps time, not utc time)
#
# @parameter  self     a TimeClass object
# @return     Modified Julian Day
# ----------------------------------------------------------------------*/
sub get_mjd {
  my $self = shift;
  $self->_create_gps_breakdown();

  my $m = $self->{"gps month"};
  my $y = $self->{"gps year"};
  if ($m <= 2) {
    $m += 12;
    $y -= 1;
  }

  my $day = $self->{"gps day"} +
            $self->{"gps hour"}/24 +
            $self->{"gps minute"}/1440 +
	    $self->{"gps second"}/86400;

  return (int(365.25  * $y) + 
	  int(30.6001 * ($m + 1))
	  + $day + 1_720_981.5 - 2_400_000.5);
}


#/**----------------------------------------------------------------------    
# @name  get_gps_breakdown
#
# Get GPS time broken down
#
# @parameter  self     a TimeClass object
# @return     gps year, month, day, hour, minute and second 
# ----------------------------------------------------------------------*/
sub get_gps_breakdown {
    my $self = shift;
    $self->_create_gps_breakdown();
    return ($self->{"gps year"},
            $self->{"gps month"},
            $self->{"gps day"},
            $self->{"gps hour"},
            $self->{"gps minute"},
            $self->{"gps second"});

}


#/**----------------------------------------------------------------------    
# @name  find_dayofyr
#
# convert year, month, day to day of year
#
# @parameter  year (4 digit)
# @           month (1-12)
# @           day   (1-31)
# @return     day of year (1-366)
# ----------------------------------------------------------------------*/
sub find_dayofyr {

    my($year,$month,$date) = @_;  # get parms
    my($i,$feb,@months,$dayofyear);      # other local variables

    $feb = 28;
    if ($year % 4 == 0) {$feb = 29;}; 
    if ($year % 100 == 0) {$feb = 28;};
    if ($year % 400 == 0) {$feb = 29;};
    @months = (0, 31, $feb, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31);

    $dayofyear = 0;
    for ($i = 1; $i < $month; $i++) {
	$dayofyear += $months[$i];
    }
    $dayofyear += $date;

    $dayofyear;
}


#/**----------------------------------------------------------------------    
# @name  find_date
#
# convert year, doy to month and date
#
# @parameter  year
# @           doy
# @return     month, day
# ----------------------------------------------------------------------*/
sub find_date {

    my($yr, $doy) = @_;  # get parms
    my($i,$feb,@months);      # other local variables

    $feb = 28;
    if    ($yr % 4   == 0) {$feb = 29;} 
    if    ($yr % 100 == 0) {$feb = 28;} 
    if    ($yr % 400 == 0) {$feb = 29;} 
    @months = (0, 31, $feb, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31);

    for ($i = 1; $i <= 12; $i++) {
	last if ($doy <= $months[$i]);
	$doy -= $months[$i];
    }
    my $month = $i;
    return ($month, $doy);
}


#--------------------------------------------------------------------------------------
## Utility routines (internal use only)
#--------------------------------------------------------------------------------------

# Clear out TimeClass object
sub _reset
{
    my $self = shift;

    undef %$self;
}

# 
# Set gps year, month, day, etc. from unix or gps time
# 
sub _create_gps_breakdown
{
    my $self = shift;
    return if exists $self->{"gps second"};
    my @mkta = gmtime($self->get_gps + $TimeClass::GPSSEC);
    $self->{"gps second"} = $mkta[0];
    $self->{"gps minute"} = $mkta[1];
    $self->{"gps hour"} = $mkta[2];
    $self->{"gps day"} = $mkta[3];
    $self->{"gps month"} = $mkta[4] + 1;
    $self->{"gps year"} = $mkta[5] + 1900;
    $self->{"gps doy"} = $mkta[7] + 1;
    return $self;
}

1;
