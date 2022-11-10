/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_memmove.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: fgomes-s <fgomes-s@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2022/10/28 14:56:32 by fgomes-s          #+#    #+#             */
/*   Updated: 2022/11/08 11:22:13 by fgomes-s         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void *ft_memmove(void *dst, const void *src, size_t n)
{
    size_t x;
    char    *ptr1;
    char    *ptr2;

    ptr1 = (char *)dst;
    ptr2 = (char *)src;
    if (ptr1 < ptr2)
    {
        x = 0;
        while (x < n)
        {
            ptr1[x] = ptr2[x];
            x++;
        }
    }
    else if (ptr1 > ptr2)
    {
        x = n;
        while (x > 0)
        {
            ptr1[x - 1] = ptr2[x - 1];
            x--;
        }
    }
    return(dst);
}
