#!/usr/bin/env bash

while read CMD; do
  # each command begins with *{number arguments in command}\r\n
  XS="${CMD}"
  set -- $XS
  printf "*${#}\r\n"
  # for each argument, we append ${length}\r\n{argument}\r\n
  for X in $CMD; do
    printf "\$${#X}\r\n$X\r\n"
  done
done