/*
 * Exercise 1.6: Explain whether the following program fragment is legal. 
 * std::cout << "The sum of " << v1;
 * << " and " << v2;
 * << " is " << v1 + v2 << std::endl;
 * If the program is legal, what does it do? If the program is not legal, why not? How
 * would you fix it?
 */


/*
 * Answer: No correct because either the first line must not use ";" at the end
 * or there should be "std::cout" at each line 
 */

//correct code is as follow

#include <iostream>
int main(){

	int v1 = 123, v2 = 343;

	std::cout << "The sum of " << v1
		<< " and " << v2
		<< " is " << v1 + v2 << std::endl;
	//or
	 
	std::cout << "The sum of " << v1;
	std::cout << " and " << v2;
	std::cout << " is " << v1 + v2 << std::endl;

	return 0;
}
