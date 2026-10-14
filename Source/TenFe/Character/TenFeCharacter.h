#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "TenFeCharacter.generated.h"

class UCameraComponent;
class USpringArmComponent;
class UStaticMeshComponent;
class UTenFeEquipmentComponent;
class UTenFeEquipmentMenuWidget;
class UTenFeHUDWidget;
class UTenFeStatsComponent;

UCLASS()
class TENFE_API ATenFeCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    ATenFeCharacter();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
    virtual float TakeDamage(float DamageAmount, struct FDamageEvent const& DamageEvent, AController* EventInstigator, AActor* DamageCauser) override;

    UFUNCTION(BlueprintCallable, Category="Ten Fe|UI")
    void ToggleEquipmentMenu();

    UFUNCTION(BlueprintPure, Category="Ten Fe|Components")
    UTenFeStatsComponent* GetStats() const { return Stats; }

    UFUNCTION(BlueprintPure, Category="Ten Fe|Components")
    UTenFeEquipmentComponent* GetEquipment() const { return Equipment; }

private:
    void MoveForward(float Value);
    void MoveRight(float Value);
    void StartSprint();
    void StopSprint();
    void PerformAttack();
    void CycleWeapon();

    UFUNCTION()
    void HandleDeath();

    UFUNCTION()
    void RefreshWeaponVisual();

    UPROPERTY(VisibleAnywhere, Category="Ten Fe|Camera")
    TObjectPtr<USpringArmComponent> CameraBoom;

    UPROPERTY(VisibleAnywhere, Category="Ten Fe|Camera")
    TObjectPtr<UCameraComponent> FollowCamera;

    UPROPERTY(VisibleAnywhere, Category="Ten Fe|Visual")
    TObjectPtr<UStaticMeshComponent> BodyVisual;

    UPROPERTY(VisibleAnywhere, Category="Ten Fe|Visual")
    TObjectPtr<UStaticMeshComponent> WeaponVisual;

    UPROPERTY(VisibleAnywhere, Category="Ten Fe|Components")
    TObjectPtr<UTenFeStatsComponent> Stats;

    UPROPERTY(VisibleAnywhere, Category="Ten Fe|Components")
    TObjectPtr<UTenFeEquipmentComponent> Equipment;

    UPROPERTY()
    TObjectPtr<UTenFeHUDWidget> HUDWidget;

    UPROPERTY()
    TObjectPtr<UTenFeEquipmentMenuWidget> EquipmentMenuWidget;

    bool bSprinting = false;
    bool bEquipmentMenuOpen = false;
    bool bAttackOnCooldown = false;
    float BaseWalkSpeed = 420.0f;
};
