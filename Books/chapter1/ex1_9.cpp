/*
 * Exercise 1.9: Write a program that uses a while to sum the numbers from 50 to 100.
 */

#include <iostream>
int main(){

	int sum = 50, count=50;
	while (count < 100){
		count ++;
		sum += count;
	}
	std::cout << "Sum of 50 to 100 inclusive is "
		<< sum << std::endl;

	return 0;
}
