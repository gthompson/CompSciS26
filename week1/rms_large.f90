program rms_large
  implicit none

  integer, parameter :: n = 10000000
  integer :: i
  real(8), allocatable :: signal(:)
  real(8) :: sumsq, rms

  allocate(signal(n))

  ! Fill signal
  do i = 1, n
     signal(i) = sin(0.001d0 * dble(i))
  end do

  ! Compute RMS
  sumsq = 0.0d0
  do i = 1, n
     sumsq = sumsq + signal(i) * signal(i)
  end do

  rms = sqrt(sumsq / dble(n))

  print *, "Samples:", n
  print *, "RMS amplitude:", rms

  deallocate(signal)
end program rms_large