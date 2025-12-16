/*
 * Exercise 1.5: We wrote the output in one large statement. 
 * Rewrite the program to use a separate statement to print each operand.
 */

#include<iostream>
int main(){
	std::cout << "Enter tow numbers:" << std::endl;
	int v1 = 0, v2 = 0;
	std::cin >> v1 >> v2;
	std::cout << "The product of ";
	std::cout << v1 << " and " << v2; 
	std::cout << " is " << v1 * v2 << std::endl;	
	return 0;
}
