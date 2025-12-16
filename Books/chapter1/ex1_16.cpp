/*
 * Exercise 1.16: Write your own version of a program that prints the sum of a set of integers read from cin.
 */

#include <iostream>
int main(){

	int summ = 0, value;
	while(std::cin >> value)
		summ += value;
	std::cout << summ << std::endl;

	return 0;
}
