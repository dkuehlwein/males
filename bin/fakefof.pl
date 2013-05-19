#!/usr/bin/perl -w
#
# Run as:
#
# ./fakefof.pl AGT028^1.p > AGT028^1.fof
#
# Fake that a TPTP formula is a FOF formula with the same symbols,
# so we can use E's version of SInE.

# put here the path to GetSymbols
my $getsymbols = "GetSymbols";

use IPC::Open2;
my @lines = <>;

my $conj = '';

foreach my $_ (@lines) { if(m/\( *([^ ,]+) *, *conjecture */) {$conj = $1}}

my $pid = open2(*READER,*WRITER,"$getsymbols --");

print WRITER (@lines);
close(WRITER);

my $dollar='$';

while(<READER>)
{
  s/$dollar/dollar_/g;
  m/^symbols\( *([^ ,]+) *, *\[(.*)\] *, *\[(.*)\] *\)\./
    or die "Bad symbols info: $_";
  my ($ref, $psyms, $fsyms) = ($1, $2, $3);
  my @psyms = split(/\,/, $psyms);
  my @fsyms = split(/\,/, $fsyms);
  my @allsyms = (@psyms, @fsyms);
  my @all1=(); 
  foreach my $sym (@allsyms) 
  {
    $sym =~ m/^ *([^\/]+)[\/].*/ or die "Bad symbol $sym in $_";
    my $s1 = $1;
    if($s1 eq '~') {$s1 = 'tptp_not'}
    elsif($s1 eq '&') {$s1 = 'tptp_and'}
    elsif($s1 eq '=>') {$s1 = 'tptp_implies'}
    elsif($s1 eq '<=>') {$s1 = 'tptp_iff'}
    elsif($s1 eq '|') {$s1 = 'tptp_or'}
    elsif($s1 eq '!') {$s1 = 'tptp_for'}
    elsif($s1 eq '?') {$s1 = 'tptp_ex'}
    push(@all1,$s1);
  }

  my $fof = "(" . join("|",@all1) .")";
  my $status = ($ref eq $conj)? 'conjecture':'axiom';
  print "fof($ref,$status,$fof).\n";
}
