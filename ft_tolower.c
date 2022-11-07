/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_tolower.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: fgomes-s <fgomes-s@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2022/10/26 16:39:11 by fgomes-s          #+#    #+#             */
/*   Updated: 2022/10/28 11:51:48 by fgomes-s         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "stddef.h"

int ft_tolower(int c)
{
    if (c > 64 && c < 91)
    {
        return (c + 32);
    }
    else
            return (c);
}