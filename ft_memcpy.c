/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_memcpy.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: fgomes-s <fgomes-s@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2022/10/28 13:10:57 by fgomes-s          #+#    #+#             */
/*   Updated: 2022/10/28 15:26:36 by fgomes-s         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "stddef.h"

void *ft_memcpy(void *dest, const void *src, size_t n)
{
    int i;
    
    i = 0;
    {
        if (!src && !dest)
        {
            return (0);
        }
        while (i < n)
        {
           ((unsigned char *)dest)[i] = ((unsigned char *)src)[i];
           i++;
        }
        return (dest);
    }
}
