#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "TenFeEnemy.generated.h"

class UStaticMeshComponent;
class UTenFeStatsComponent;
class UTextRenderComponent;

UCLASS()
class TENFE_API ATenFeEnemy : public ACharacter
{
    GENERATED_BODY()

public:
    ATenFeEnemy();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;
    virtual float TakeDamage(float DamageAmount, struct FDamageEvent const& DamageEvent, AController* EventInstigator, AActor* DamageCauser) override;

private:
    void AcquireTarget();
    void ChaseTarget();
    void BeginAttack();
    void ResolveAttack();
    void FinishAttackRecovery();
    void UpdateStatusLabel(const FString& StateLabel);
    void FaceStatusLabelToPlayer() const;

    UFUNCTION()
    void HandleDeath();

    void RespawnEnemy();

    UPROPERTY(VisibleAnywhere, Category="Ten Fe|Enemy")
    TObjectPtr<UStaticMeshComponent> BodyVisual;

    UPROPERTY(VisibleAnywhere, Category="Ten Fe|Enemy")
    TObjectPtr<UStaticMeshComponent> WeaponVisual;

    UPROPERTY(VisibleAnywhere, Category="Ten Fe|Enemy")
    TObjectPtr<UTextRenderComponent> StatusLabel;

    UPROPERTY(VisibleAnywhere, Category="Ten Fe|Enemy")
    TObjectPtr<UTenFeStatsComponent> Stats;

    UPROPERTY()
    TObjectPtr<ACharacter> TargetCharacter;

    UPROPERTY(EditDefaultsOnly, Category="Ten Fe|Enemy", meta=(ClampMin="100.0"))
    float DetectionRange = 900.0f;

    UPROPERTY(EditDefaultsOnly, Category="Ten Fe|Enemy", meta=(ClampMin="50.0"))
    float AttackRange = 145.0f;

    UPROPERTY(EditDefaultsOnly, Category="Ten Fe|Enemy", meta=(ClampMin="0.0"))
    float AttackDamage = 22.0f;

    UPROPERTY(EditDefaultsOnly, Category="Ten Fe|Enemy", meta=(ClampMin="0.1"))
    float AttackWindup = 0.65f;

    UPROPERTY(EditDefaultsOnly, Category="Ten Fe|Enemy", meta=(ClampMin="0.1"))
    float AttackCooldown = 1.4f;

    FTransform SpawnTransform;
    FTimerHandle AttackWindupHandle;
    FTimerHandle AttackRecoveryHandle;
    FTimerHandle RespawnHandle;
    bool bCanAttack = true;
    bool bWindingUp = false;
    bool bDead = false;
};
