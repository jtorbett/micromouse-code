/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2024 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32f4xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

void HAL_TIM_MspPostInit(TIM_HandleTypeDef *htim);

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define VL53L4CD_INT_Pin GPIO_PIN_13
#define VL53L4CD_INT_GPIO_Port GPIOC
#define IR_FRONT_L_Pin GPIO_PIN_0
#define IR_FRONT_L_GPIO_Port GPIOC
#define IR_FRONT_R_Pin GPIO_PIN_1
#define IR_FRONT_R_GPIO_Port GPIOC
#define IR_L_Pin GPIO_PIN_2
#define IR_L_GPIO_Port GPIOC
#define IR_R_Pin GPIO_PIN_3
#define IR_R_GPIO_Port GPIOC
#define SW1_Pin GPIO_PIN_0
#define SW1_GPIO_Port GPIOA
#define SW2_Pin GPIO_PIN_1
#define SW2_GPIO_Port GPIOA
#define VBATT_MON_Pin GPIO_PIN_4
#define VBATT_MON_GPIO_Port GPIOA
#define L_ENC_A_Pin GPIO_PIN_6
#define L_ENC_A_GPIO_Port GPIOA
#define L_ENC_B_Pin GPIO_PIN_7
#define L_ENC_B_GPIO_Port GPIOA
#define IR_FRONT_L_PULSE_Pin GPIO_PIN_0
#define IR_FRONT_L_PULSE_GPIO_Port GPIOB
#define IR_FRONT_R_PULSE_Pin GPIO_PIN_1
#define IR_FRONT_R_PULSE_GPIO_Port GPIOB
#define IR_L_PULSE_Pin GPIO_PIN_2
#define IR_L_PULSE_GPIO_Port GPIOB
#define ICM_42688_SCK_Pin GPIO_PIN_10
#define ICM_42688_SCK_GPIO_Port GPIOB
#define ICM_42688_CS_Pin GPIO_PIN_13
#define ICM_42688_CS_GPIO_Port GPIOB
#define ICM_42688_MISO_Pin GPIO_PIN_14
#define ICM_42688_MISO_GPIO_Port GPIOB
#define ICM_42688_MOSI_Pin GPIO_PIN_15
#define ICM_42688_MOSI_GPIO_Port GPIOB
#define ICM_42688_INT1_Pin GPIO_PIN_6
#define ICM_42688_INT1_GPIO_Port GPIOC
#define ICM_42688_INT2_Pin GPIO_PIN_7
#define ICM_42688_INT2_GPIO_Port GPIOC
#define MOTORS_EN_Pin GPIO_PIN_9
#define MOTORS_EN_GPIO_Port GPIOC
#define LMOTOR_A_Pin GPIO_PIN_8
#define LMOTOR_A_GPIO_Port GPIOA
#define LMOTOR_B_Pin GPIO_PIN_9
#define LMOTOR_B_GPIO_Port GPIOA
#define RMOTOR_A_Pin GPIO_PIN_10
#define RMOTOR_A_GPIO_Port GPIOA
#define RMOTOR_B_Pin GPIO_PIN_11
#define RMOTOR_B_GPIO_Port GPIOA
#define SWDIO_Pin GPIO_PIN_13
#define SWDIO_GPIO_Port GPIOA
#define SWCLK_Pin GPIO_PIN_14
#define SWCLK_GPIO_Port GPIOA
#define LED1_Pin GPIO_PIN_10
#define LED1_GPIO_Port GPIOC
#define LED2_Pin GPIO_PIN_11
#define LED2_GPIO_Port GPIOC
#define IR_R_PULSE_Pin GPIO_PIN_3
#define IR_R_PULSE_GPIO_Port GPIOB
#define VL53L4CD_EN_Pin GPIO_PIN_5
#define VL53L4CD_EN_GPIO_Port GPIOB
#define R_ENC_A_Pin GPIO_PIN_6
#define R_ENC_A_GPIO_Port GPIOB
#define R_ENC_B_Pin GPIO_PIN_7
#define R_ENC_B_GPIO_Port GPIOB
#define VL53L4CD_SCL_Pin GPIO_PIN_8
#define VL53L4CD_SCL_GPIO_Port GPIOB
#define VL53L4CD_SDA_Pin GPIO_PIN_9
#define VL53L4CD_SDA_GPIO_Port GPIOB

/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
