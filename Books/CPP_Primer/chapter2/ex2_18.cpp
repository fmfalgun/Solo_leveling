// Exercise 2.18: Write code to change the value of a pointer. Write code to change the
// value to which the pointer points. 

#include <iostream>

int main(){

	int var1 = 10, var2 = 20;
	int *p1 = &var1;
	std::cout << p1 << std::endl;
	p1 = &var2;
	std::cout << p1 << std::endl;
	*p1 = 30;
	std::cout << p1 << " " << *p1 << " " << var1 << " " << var2 << std::endl;	

	return 0;
}
