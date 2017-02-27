#!/usr/bin/perl

use strict;
use Env;

my ($queue,$walltime) = ($0 =~ /submit_(\w+)_(\d+)\.pl/);

if ( @ARGV < 1 ) {
        die "Usage: $0 [-j job_name] [-o output_path] [-e error_path] <program> [arguments]...\n";
}

my $job_name = "";
my $output_directive = "";
my $error_directive = "";
while ($ARGV[0] =~ /^-/)
  {
  if ($ARGV[0] =~ /^-j/)
    { 
    shift @ARGV;
    $job_name = shift @ARGV; 
    }
  elsif ($ARGV[0] =~ /^-o/)
    {
    shift @ARGV;
    my $path = shift @ARGV;
    $output_directive = "#PBS -o $path";
    }
  elsif ($ARGV[0] =~ /^-e/)
    {
    shift @ARGV;
    my $path = shift @ARGV;
    $error_directive = "#PBS -e $path";
    }
  else
    {
    print STDERR "Unknown option \"",$ARGV[0],"\"\n";
    die "Usage: $0 [-j job_name] [-o output_path] [-e error_path] <program> [arguments]...\n";
    }
  }

if ($job_name eq "")
  {
  $job_name = "pbs_" . $ARGV[0];
  }  


  
if ($walltime < 10)
  { $walltime = "0" . $walltime; }

my $command = join(" ", @ARGV);
$command =~ s/\"/\\\"/g;
$job_name =~ s/\W+/_/g;
my $command_string = $command;
$command_string =~ s/\'/\\\'/g;
$job_name = substr($job_name,0,15);
my $user_name = `whoami`; chomp $user_name;

my $sub_env = "";
if (exists $ENV{PBS_SUB_ENVIRONMENT})
  { $sub_env = `echo -e \$PBS_SUB_ENVIRONMENT`; }

my $pbs_string = "
#!/bin/tcsh
#PBS -q $queue
#PBS -l nodes=1:ppn=1,walltime=$walltime\:00:00
#PBS -u $user_name
#PBS -S /bin/bash
#PBS -N $job_name
$output_directive
$error_directive
#
# This is a short sample of submission to PBS. The important part is up
# fater PBS keyword, defining the user name, the shell to use and the
# name to be assigned to the calc (it has a 14 character limitation)
# For more info look into man pages, man qsub
#
cd \\\$PBS_O_WORKDIR
HOME=/mlab/data/$user_name
PATH=\\\${PATH}:/mlab/data/$user_name/bin
$sub_env
date
echo 'started \[$command_string\]'
echo '----------------\n'

$command

echo '\n----------------'
echo 'finished \[$command_string\]'
date

";

if (-e "/usr/local/bin/qsub")
  { system("echo \"$pbs_string\" | /usr/local/bin/qsub"); }
elsif (-e "/usr/bin/qsub")
  { system("echo \"$pbs_string\" | /usr/bin/qsub"); }
else
  { system("echo \"$pbs_string\" | /mlab/data/software/bin/qsub"); }

exit 0;

