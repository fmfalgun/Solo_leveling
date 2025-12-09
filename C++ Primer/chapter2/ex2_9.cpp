/*
 * Exercise 2.9: Explain the following definitions. For those that are illegal, 
 * explain what’s wrong and how to correct it.
 * 	(a) std::cin >> int input_value; (b) int i = { 3.14 };
 * 	(c) double salary = wage = 9999.99; (d) int i = 3.14;
 */

// Answer: 
// 	a - input_value of type int (illegal,  coz >> operator expects existing variable)
// 	b - i of type int (illegal coz list initialization disallows narrowing conversion))
// 	c - salary and wage of type double int (illegal coz wage is declaring and defining at same time)
// 	d - i of type int (Legal because i becomes 3 after conversion, method is not correct)

// Correct callings
#include <iostream>
int main(){

	int input_value;
	std::cin >> input_value;
	int i = 3.14;
	double wage = 9999.99;
	double salary = wage;
	i = 3.14;
	std::cout << i << std::endl;
	std::cout << wage << std::endl;
	std::cout << salary << std::endl;
	std::cout << i << std::endl;

	return 0;
}
