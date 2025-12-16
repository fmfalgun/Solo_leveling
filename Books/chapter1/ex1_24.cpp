/*
 * Exercise 1.24: Test the previous program by giving multiple transactions representing
 * multiple ISBNs. The records for each ISBN should be grouped together.
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

/*
 * Results:
 *
 * input - cat intput.txt
 * book1 3 20.00
 * book1 3 20.00
 * book2 3 20.00
 * book2 2 25.00
 * book3 2 25.00
 * book3 2 25.00
 *
 * output - cat output.txt
 * book1 6 120 20 this item have total 2 trnxs.
 * book2 5 110 22 this item have total 2 trnxs.
 * book3 4 100 25 this item have total 2 trnxs.
 */
