/*
 * Exercise 1.23: Write a program that reads several transactions and 
 * counts how many transactions occur for each ISBN.
 */

#include <iostream>
#include "Sales_item.h"
int main (){

	Sales_item item, newitem;
	int count = 1;
	std::cin >> item;
	while(std::cin >> newitem)
	{
		if (newitem.isbn() == item.isbn()) {
			count++;
			item += newitem;
		}
		else{
			std::cout << item << " this item have total " << count << " trnxs." << std::endl;
			count = 1;
			item = newitem;
		}
	}
	std::cout << item << " this item have total " << count << " trnxs." << std::endl;
	return 0;
}
