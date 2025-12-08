/*
 * Exercise 1.12: What does the following for loop do? What is the final value of sum? 
 * 	int sum = 0;
 * 	for (int i = -100; i <= 100; ++i) 
 * 		sum += i;
 */

// Answer: going to add value from -100 to 0 in variable "sum"
// and then going to add value from 0 to 100 in same variable
// which will result as zero value in variable "sum" at the end

#include <iostream>
int main(){

	int sum = 0;
	for (int i = -100; i<= 100; i++)
		sum += i;
	std::cout << sum << std::endl;

	return 0;
}
