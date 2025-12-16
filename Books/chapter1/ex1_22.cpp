/*
 * Exercise 1.22: Write a program that reads several transactions for the same ISBN.
 * Write the sum of all the transactions that were read.
 */

#include <iostream>
#include "Sales_item.h"
int main(){

	Sales_item item, temp;
	std::cin >> item;
	while(std::cin >> temp)
		item = item + temp;
	std::cout << item << std::endl;
	return 0;
}
