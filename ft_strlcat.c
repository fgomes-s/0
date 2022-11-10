/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strlcat.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: fgomes-s <fgomes-s@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2022/10/26 13:42:32 by fgomes-s          #+#    #+#             */
/*   Updated: 2022/11/08 11:21:43 by fgomes-s         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

size_t ft_strlcat(char *dest, const char *src, size_t size)
{
    int i;
    i = 0;
    int dlen;
    while (dest[dlen])
    {
    dlen++;
    }
    while (i <= size)
    {
        ((unsigned char *)dest)[dlen] = ((unsigned char *)src)[i];
        i++;
        dlen++;
    }
    return(0);
}
