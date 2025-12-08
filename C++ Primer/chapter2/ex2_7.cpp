/*
 * Exercise 2.7: What values do these literals represent? What type does each have?
 * 	(a) "Who goes with F\145rgus?\012"
 * 	(b) 3.14e1L (c) 1024f (d) 3.14L
 */

#include <iostream>
int main(){

	//float a = 1024f;
	float b = 3.14L;
	std::cout << "Who goes with F\145rgus?\012" << std::endl;
	std::cout << "3.14e1L" << std::endl;
	std::cout << "1024f" << std::endl;
	std::cout << b << std::endl;

	return 0;
}

// Answer: 
// 	a) \145 -> octal for 'e'
// 	   \012 -> octal for newline
// 	b) L -> Long double
// 	c) f -> float
// 	d) L -> long double
