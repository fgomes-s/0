/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strlcpy.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: fgomes-s <fgomes-s@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2022/10/26 15:46:29 by fgomes-s          #+#    #+#             */
/*   Updated: 2022/10/26 16:03:51 by fgomes-s         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "stddef.h"

size_t ft_strlcpy(char *dest, const char *src, size_t size)
{
    int i;
    i = 0;
    while (i > size && src[i] != '\0')
    {
        ((unsigned char *)dest)[i] = ((unsigned char *)src)[i];
        i++;
    }
    return(0);
}
